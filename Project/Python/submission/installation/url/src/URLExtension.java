package org.nlogo.extensions.url;

import java.awt.image.BufferedImage ;
import java.io.BufferedInputStream ;
import java.io.ByteArrayInputStream ;
import java.io.ByteArrayOutputStream ;
import java.io.File ;
import java.io.FileInputStream ;
import java.io.IOException ;
import java.io.InputStream ;
import java.net.URISyntaxException ;
import java.net.URL ;
import java.net.URLConnection ;
import java.util.Scanner ;

import javax.imageio.ImageIO ;

import com.myjavatools.web.ClientHttpRequest ;

import org.nlogo.api.Argument ;
import org.nlogo.api.Context ;
import org.nlogo.api.DefaultClassManager;
import org.nlogo.api.DefaultReporter ;
import org.nlogo.api.ExtensionException ;
import org.nlogo.api.LogoException ;
import org.nlogo.api.LogoList ;
import org.nlogo.api.PrimitiveManager;
import org.nlogo.api.Syntax ;

public class URLExtension extends DefaultClassManager {
    @Override
	public void load(PrimitiveManager primitiveManager) 
	{
        primitiveManager.addPrimitive( "percent-escape" , new PercentEscape() ) ;
        primitiveManager.addPrimitive( "get" , new Get() ) ;
        primitiveManager.addPrimitive( "post" , new Post() ) ;
        // TODO: Could also implement GET & POST with cookies. 
        // The underlying library supports it, but I don't see a pressing need.
        
        // TODO: What about getting an image back from the web server?  
        // Right now we just hand back the result as a string -- 
        //  should we do a "convert-string-to-image" primitive? would that work?
    }
    
    public static class PercentEscape extends DefaultReporter
	{
		@Override
		public Syntax getSyntax()
		{
			return Syntax.reporterSyntax
				( new int[] { Syntax.StringType() } ,
				  Syntax.StringType() ) ;
		}
		@Override
		public String getAgentClassString()
		{
			return "OTPL" ;
		}
		public Object report( Argument args[] , Context context )
			throws ExtensionException, LogoException
		{
			String urlString = args[ 0 ].getString().trim() ;
			//NOTE: doubtful this appropriately handles all cases...
			try
			{
				if (urlString.substring( 0 , 5 ).equalsIgnoreCase( "http:" ))
				{
					return new java.net.URI("http", urlString.substring(5), null).toASCIIString();
				}
				else
				{
					return new java.net.URI("http", urlString, null).toASCIIString();
				}
			}
			catch( URISyntaxException ex )
			{
				ex.printStackTrace();
				throw new ExtensionException (ex);
			}				

		}					      
    }

    public static class Get extends DefaultReporter
	{
		@Override
		public Syntax getSyntax()
		{
			return Syntax.reporterSyntax
				( new int[] { Syntax.StringType() } ,
				  Syntax.WildcardType() ) ;
		}
		@Override
		public String getAgentClassString()
		{
			return "OTPL" ;
		}
		public Object report( Argument args[] , Context context )
			throws ExtensionException, LogoException
		{
			String urlString = args[ 0 ].getString() ;
			try {				
				URL url  = new URL( urlString ) ;
				URLConnection conn = url.openConnection() ;
				Object responseObj = processResponse(conn.getInputStream());
				conn.getInputStream().close();
				return responseObj;
			} catch (Exception ex)
			{
				throw new ExtensionException(ex);
			}
		}					      
    }

    public static class Post extends DefaultReporter
	{
		@Override
		public Syntax getSyntax()
		{
			return Syntax.reporterSyntax
				( new int[] { Syntax.StringType() , Syntax.ListType() } ,
						Syntax.WildcardType()) ;
		}
		@Override
		public String getAgentClassString()
		{
			return "OTPL" ;
		}
		public void throwSyntaxError() throws ExtensionException
		{
			throw new ExtensionException("The 'parameters' input must be a list of lists, "
					+ "containing [name value] pairs (for regular post requests), or "
					+ "[name fileName imageObject] triplets (if you are uploading an image file), "
					+ "or [name fileName realFileName] (if you are uploading a file from disk). "
					+ "e.g. url:post \"http://my.com/myscript.php [[\"name\" \"Bob\"] "
					+ "[\"photo\" \"bob.png\" bitmap:grab-view] "
					+ "[\"music\" \"song.mp3\" \"Music/mysong.mp3\"]]");
		}
		public Object report( Argument args[] , Context context )
			throws ExtensionException, LogoException
		{
			String urlString = args[ 0 ].getString() ;
			LogoList params = args[1].getList();

			ClientHttpRequest req;
			try {
				req = new ClientHttpRequest(urlString);
			} 
			catch( IOException ex )
			{
				throw new ExtensionException(ex);
			}

			// get params & verify syntax
			for (Object obj : params)
			{
					if( ! ( obj instanceof LogoList ) )
					{
						throwSyntaxError() ;
					}
					LogoList lst = (LogoList) obj ;
					if( lst.size() == 2)
					{
						if (lst.get( 0 ) instanceof String)
						{
							try {
								req.setParameter( (String) lst.get( 0 ), (String) lst.get( 1 ) );
							} 
							catch (IOException ex)
							{
								throw new ExtensionException(ex);
							}
						}
						else
						{
							throw new ExtensionException( "The name in each [name value] pair must be a string.");
						}
					}
					else if (lst.size() == 3 )
					{
						if (lst.get( 0 ) instanceof String && lst.get(1) instanceof String)
						{
							if (lst.get( 2 ) instanceof String)
							{
								try {
									File f = new File((String)lst.get( 2 ));
									req.setParameter( (String) lst.get(0) , (String) lst.get( 1 ), new FileInputStream(f) );
								} catch (IOException ex)
								{
									throw new ExtensionException("Error reading from input file " + lst.get(2));
								}
							}
							else if (lst.get(2) instanceof BufferedImage) 
							{
								try {
									BufferedImage im = (BufferedImage) lst.get(2);
									ByteArrayOutputStream bos = new ByteArrayOutputStream();
									ImageIO.write( im , "png" , bos);
									bos.close();
									byte[] bytes = bos.toByteArray();
									ByteArrayInputStream bis = new ByteArrayInputStream(bytes);
									req.setParameter( (String) lst.get(0) , (String) lst.get( 1 ), bis );								
								} catch (IOException ex)
								{
									throw new ExtensionException("Error converting image into a stream of bytes to upload." );									
								}								
							}
							else
							{
								throw new ExtensionException("In a parameter triplet, the third value must either be a string that gives a valid filename, or an image object to create a file from (see 'bitmap' extension)");
							}
						}						
						else
						{
							throw new ExtensionException( "The name and filename in each [name filename image-or-filename] triplet must be a string.");
						}
					}
					else
					{
						throwSyntaxError();
					}				
			}

			try {
				InputStream serverInput = req.post();
				Object responseObj = processResponse(serverInput);
				serverInput.close();
				return responseObj;
				
//				Scanner scanner = new java.util.Scanner(serverInput);
//				String contents = scanner.useDelimiter("\\Z").next(); // slurp the whole file
//				scanner.close();
				
			} catch (IOException ex)
			{
				throw new ExtensionException(ex);
			}
		}					      
    }

    private static Object processResponse(InputStream serverInput) throws IOException
    {
		BufferedInputStream bufIn = new BufferedInputStream( serverInput );
		ByteArrayOutputStream bytesOut = new ByteArrayOutputStream();
		int n;
		while ((n = bufIn.read()) != -1) {
			bytesOut.write((byte) n);
		}
		bufIn.close();
		bytesOut.close();
		byte[] bytes = bytesOut.toByteArray();
		if (dataAppearsToBeText(bytes))
		{
			return new String(bytes);
		}
		else
		{
			try {
				ByteArrayInputStream bytesIn = new ByteArrayInputStream(bytes);
				BufferedImage img = ImageIO.read( bytesIn );
				return img;
			} catch (Exception ex)
			{
				ex.printStackTrace();
				// For now, just return text, even though it's probably wrong. 
				return new String(bytes);
			}
		}				
    }
    // Not perfect, but hopefully a reasonable heuristic for whether  
    private static boolean dataAppearsToBeText(byte[] bytes)
    {
    	int nontext = 0;
    	int text = 0;
    	// only read the first 1000 bytes, if the data is long...
    	for (int i = 0; i < bytes.length && i < 1000; i++)
    	{
    		byte b = bytes[i];
    		if ((b < 8 || b > 13) && (b < 32 || b > 126))
    		{
    			nontext++;
    		}
    		else
    		{
    			text++;
    		}
    	}
    	// if more than 95% of the characters fall in the normal text range, we'll consider it text... 
    	return (text / ((double) nontext + text) > 0.95);
    }

}
